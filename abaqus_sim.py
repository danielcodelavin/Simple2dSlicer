import abaqus as abq
from abaqus import session
import numpy as np
import matplotlib.pyplot as plt
import os


def run_abaqus_analysis(grid, numrows, numcols):
    # Create a new model
    model = abq.mdb.Model(name='ThermalGridModel')

    # Create base plate part
    s = model.ConstrainedSketch(name='BaseSketch', sheetSize=200.0)
    s.rectangle(point1=(0, 0), point2=(50, 50))
    base_part = model.Part(name='BasePart', dimensionality=abq.THREE_D, type=abq.DEFORMABLE_BODY)
    base_part.BaseSolidExtrude(sketch=s, depth=1)

    # Create cube part
    s = model.ConstrainedSketch(name='CubeSketch', sheetSize=200.0)
    s.rectangle(point1=(0, 0), point2=(1, 1))
    cube_part = model.Part(name='CubePart', dimensionality=abq.THREE_D, type=abq.DEFORMABLE_BODY)
    cube_part.BaseSolidExtrude(sketch=s, depth=1)

    # Create materials
    base_material = model.Material(name='BaseMaterial')
    base_material.Conductivity(table=((50.0,),))  # Example conductivity
    base_material.SpecificHeat(table=((500.0,),))  # Example specific heat
    base_material.Density(table=((7800.0,),))  # Example density

    copper = model.Material(name='Copper')
    copper.Conductivity(table=((400.0,),))
    copper.SpecificHeat(table=((385.0,),))
    copper.Density(table=((8960.0,),))

    bronze = model.Material(name='Bronze')
    bronze.Conductivity(table=((50.0,),))
    bronze.SpecificHeat(table=((380.0,),))
    bronze.Density(table=((8800.0,),))

    # Create sections
    model.HomogeneousSolidSection(name='BaseSection', material='BaseMaterial')
    model.HomogeneousSolidSection(name='CopperSection', material='Copper')
    model.HomogeneousSolidSection(name='BronzeSection', material='Bronze')

    # Assign base section
    base_part.SectionAssignment(region=(base_part.cells,), sectionName='BaseSection')

    # Create assembly
    assembly = model.rootAssembly
    base_instance = assembly.Instance(name='BaseInstance', part=base_part, dependent=abq.OFF)

    # Create step
    model.HeatTransferStep(name='ThermalStep', previous='Initial', timePeriod=1000.0, maxNumInc=1000, initialInc=0.1, minInc=1e-5, maxInc=10.0)

    # Apply initial temperature to base
    model.Temperature(name='BaseTemp', createStepName='Initial', region=(base_instance.cells,), distributionType=abq.UNIFORM, crossSectionDistribution=abq.CONSTANT_THROUGH_THICKNESS, magnitudes=(400.0,))

    # Create a list to store cube instances
    cube_instances = []

    # Function to create a cube instance
    def create_cube(x, y, material):
        cube_instance = assembly.Instance(name=f'Cube_{x}_{y}', part=cube_part, dependent=abq.OFF)
        cube_instance.translate(vector=(x, y, 1))
        if material == 1:
            cube_instance.cells.setValues(cellColor='red')
            section = 'CopperSection'
        else:
            cube_instance.cells.setValues(cellColor='blue')
            section = 'BronzeSection'
        cube_part.SectionAssignment(region=(cube_part.cells,), sectionName=section)
        model.Temperature(name=f'CubeTemp_{x}_{y}', createStepName='Initial', region=(cube_instance.cells,), distributionType=abq.UNIFORM, crossSectionDistribution=abq.CONSTANT_THROUGH_THICKNESS, magnitudes=(1200.0,))
        return cube_instance

    # Add cubes based on grid
    for row in range(numrows):
        for col in range(numcols):
            cell = grid[row][col]
            if cell.fill == 1 or cell.fill == 2:
                cube_instances.append(create_cube(col, row, cell.fill))

    # Create mesh
    base_part.seedPart(size=1.0)
    base_part.generateMesh()
    cube_part.seedPart(size=0.5)
    cube_part.generateMesh()

    # Define output requests
    model.FieldOutputRequest(name='F-Output-1', createStepName='ThermalStep', variables=('NT',))

    # Define history output for specific points
    # Base plate points
    base_points = [(0, 0, 0), (25, 25, 0), (50, 50, 0)]
    for i, point in enumerate(base_points):
        node = base_instance.nodes.getClosest(coordinates=point)
        model.HistoryOutputRequest(name=f'H-Output-Base-{i}', createStepName='ThermalStep', variables=('NT',), region=node)

    # Cube points (example - you may want to adjust these based on your specific grid)
    cube_points = [(0, 0, 1), (25, 25, 1), (49, 49, 1)]
    for i, point in enumerate(cube_points):
        if cube_instances:  # Check if any cubes were created
            node = cube_instances[0].nodes.getClosest(coordinates=point)
            model.HistoryOutputRequest(name=f'H-Output-Cube-{i}', createStepName='ThermalStep', variables=('NT',), region=node)

    # Create job
    job = abq.mdb.Job(name='ThermalGridAnalysis', model=model, description='Thermal analysis of 2D grid structure')
    job_name = 'ThermalGridAnalysis'
    
      # Set output request options
    job.setValues(
        outputLowPrecision=False,  # Use full precision for output
        writeRestart=abq.ON,  # Write restart files
        getMemoryFromAnalysis=abq.ON,  # Get memory usage information
        contactPrint=abq.ON,  # Include contact information in output
        historyPrint=abq.ON,  # Include history data in output
        memory=90,  # Percentage of total physical memory to use
        memoryUnits=abq.PERCENTAGE
    )

    # Create a directory for output files
    output_dir = 'abaqus_output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Submit job
    job.submit()
    job.waitForCompletion()


    # Submit job
    job.submit()
    job.waitForCompletion()


    # Save the model database
    model_name = f"{output_dir}/{job_name}.cae"
    abq.mdb.saveAs(pathName=model_name)
    print(f"Model database saved as {model_name}")

    # Save the output database
    odb_name = f"{job_name}.odb"
    if os.path.exists(odb_name):
        os.rename(odb_name, f"{output_dir}/{odb_name}")
        print(f"Output database saved as {output_dir}/{odb_name}")
    else:
        print("Warning: ODB file not found. Check Abaqus log for errors.")

    # Copy other output files
    output_extensions = ['.dat', '.msg', '.sta', '.sim', '.inp', '.log', '.prt', '.com']
    for ext in output_extensions:
        src_file = f"{job_name}{ext}"
        if os.path.exists(src_file):
            os.rename(src_file, f"{output_dir}/{src_file}")
            print(f"Copied {src_file} to {output_dir}/")
        else:
            print(f"Warning: {src_file} not found.")

    # Save a copy of the grid data
    with open(f"{output_dir}/grid_data.txt", 'w') as f:
        for row in range(numrows):
            for col in range(numcols):
                f.write(f"{row},{col},{grid[row][col].fill}\n")
    print(f"Grid data saved to {output_dir}/grid_data.txt")

    print("All output files have been saved to the 'abaqus_output' directory.")

    # Perform post-processing
    post_process_results(job_name, output_dir)

def post_process_results(job_name, output_dir):
    from abaqus import session
    import numpy as np
    import matplotlib.pyplot as plt

    # Open the output database
    odb_path = os.path.join(output_dir, job_name + '.odb')
    odb = session.openOdb(name=odb_path)
    
    # Get the step
    step = odb.steps['ThermalStep']
    
    # Initialize lists to store data
    times = []
    base_temps = [[] for _ in range(3)]
    cube_temps = [[] for _ in range(3)]
    
    # Extract history output data
    for i in range(3):
        base_region = step.historyRegions[f'Node BASEINSTANCE.{i+1}']
        base_data = base_region.historyOutputs['NT11'].data
        for time, temp in base_data:
            times.append(time)
            base_temps[i].append(temp)
        
        if f'Node CUBE_0_0.{i+1}' in step.historyRegions:
            cube_region = step.historyRegions[f'Node CUBE_0_0.{i+1}']
            cube_data = cube_region.historyOutputs['NT11'].data
            for _, temp in cube_data:
                cube_temps[i].append(temp)
    
    # Close the output database
    odb.close()
    
    # Plot the results
    plt.figure(figsize=(10, 6))
    for i in range(3):
        plt.plot(times, base_temps[i], label=f'Base Point {i+1}')
        if cube_temps[i]:
            plt.plot(times, cube_temps[i], label=f'Cube Point {i+1}')
    
    plt.xlabel('Time')
    plt.ylabel('Temperature')
    plt.title('Temperature vs Time at Various Points')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, 'temperature_plot.png'))
    plt.close()
    
    # Save numerical data
    np.savetxt(os.path.join(output_dir, 'time_data.csv'), times, delimiter=',')
    np.savetxt(os.path.join(output_dir, 'base_temp_data.csv'), np.array(base_temps).T, delimiter=',')
    np.savetxt(os.path.join(output_dir, 'cube_temp_data.csv'), np.array(cube_temps).T, delimiter=',')
    
    print("Post-processing completed. Results saved in the output directory.")
print("Abaqus thermal analysis completed.")

# if __name__ == "__main__":
#     # This is a placeholder for testing. You'll need to pass actual grid data here.
#     class Cell:
#         def __init__(self, master, x, y, size):
#             self.fill = 0
    
#     test_grid = [[Cell(None, i, j, 1) for j in range(10)] for i in range(10)]
#     # Set some cells to filled state
#     test_grid[0][0].fill = 1
#     test_grid[5][5].fill = 2
#     test_grid[9][9].fill = 1
    
#     run_abaqus_analysis(test_grid, 10, 10)