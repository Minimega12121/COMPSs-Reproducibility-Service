import random
from pycompss.api.task import task
from pycompss.api.api import compss_wait_on
from pycompss.api.parameter import *
import os

@task(returns=tuple)
def count_points_in_circle(num_points:int):
    """ Genreates random points and counts the number of points that fall within the unit circle.

    Args:
        num_points (int): number of points to generate

    Returns: 
        None
    """
    count = 0
    points = []
    for _ in range(num_points):
        x = random.random()
        y = random.random()
        points.append((x, y))
        if x**2 + y**2 <= 1.0:
            count += 1
    return count, points

@task(returns=None, filename = FILE_OUT)
def write_points_to_file(points, filename):
    """ Writes points to a file
    Args:
        points (list): list of points to write to file
        filename (str): path to file to write points to
    """
    with open(filename, 'w') as f:
        for point in points:
            f.write(f"{point[0]}, {point[1]}\n")

def main(num_points, num_tasks):
    points_per_task = num_points // num_tasks
    
    # Launch tasks in parallel
    results = [count_points_in_circle(points_per_task) for i in range(num_tasks)]
    
    # Wait for all count tasks to complete and get the results
    results = compss_wait_on(results)
    
    total_points_in_circle = 0
    
    if not os.path.isdir("output"):
        os.mkdir("output")
        
    for i, (count, points) in enumerate(results):
        total_points_in_circle += count
        # Write points to file in parallel
        filename = f"./output/{i}.txt"
        write_points_to_file(points, filename)
    
    # Aggregate results
    total_points = points_per_task * num_tasks
    
    # Estimate Pi
    pi_estimate = (4.0 * total_points_in_circle) / total_points
    
    # Write Pi estimate to a file
    with open("./output/Result.txt", 'w') as f:
        f.write(f"Estimated Pi: {pi_estimate}\n")
    
    print(f"Estimated Pi: {pi_estimate}")

if __name__ == '__main__':
    import sys
    num_points = int(sys.argv[1]) if len(sys.argv) > 1 else 1000000
    num_tasks = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    if num_tasks > num_points:
        raise Exception("Please provide more points than tasks.")
    main(num_points, num_tasks)
