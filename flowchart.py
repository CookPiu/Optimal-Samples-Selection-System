from graphviz import Digraph


# Create a flowchart for the Greedy algorithm
def create_greedy_flowchart():
    dot = Digraph(comment='Greedy Algorithm')

    dot.node('A', 'Start')
    dot.node('B', 'Generate k and j combinations')
    dot.node('C', 'Generate s subgroups for each j group')
    dot.node('D', 'Track coverage of each j group')
    dot.node('E', 'Are all j groups covered?')
    dot.node('F', 'Select k group that covers max unsatisfied j groups')
    dot.node('G', 'Add k group to selected')
    dot.node('H', 'Output selected k groups')

    dot.edges(['AB', 'BC', 'CD', 'DE'])
    dot.edge('E', 'F', label='No')
    dot.edge('E', 'H', label='Yes')
    dot.edge('F', 'G')
    dot.edge('G', 'D')

    return dot


# Create a flowchart for the ILP algorithm
def create_ilp_flowchart():
    dot = Digraph(comment='ILP Algorithm')

    dot.node('A', 'Start')
    dot.node('B', 'Generate k and j combinations')
    dot.node('C', 'Generate s subgroups for each j group')
    dot.node('D', 'Formulate ILP model')
    dot.node('E', 'Solve ILP')
    dot.node('F', 'Is the solution optimal?')
    dot.node('G', 'Output selected k groups')

    dot.edges(['AB', 'BC', 'CD', 'DE'])
    dot.edge('E', 'F', label='Not optimal')
    dot.edge('F', 'G', label='Optimal')

    return dot


# Generate and render the flowcharts as images
greedy_flowchart = create_greedy_flowchart()
greedy_flowchart.render('greedy_algorithm_flowchart', format='png', cleanup=True)  # This will generate a PNG image

ilp_flowchart = create_ilp_flowchart()
ilp_flowchart.render('ilp_algorithm_flowchart', format='png', cleanup=True)  # This will generate a PNG image
