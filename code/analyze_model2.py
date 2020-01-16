"""
This module allows the analysis of a simulation generated with a model2 file.
It computes several analysis files to understand the problems in the
simulation.
"""
import textwrap
import argparse


def args_parse():
    """
    Parses the given arguments when function is called.
        - Modified Model2 file
        - New Poe file
        - New Por file
        - Node annotation file
    Returns :
        - The four mandatory arguments as arguments
    """
    parser = argparse.ArgumentParser()
    # Argument for Modified Model2 file
    parser.add_argument("m2", metavar="MODEL2",
                        help="Enter a valid model 2 file")
    # Argument for New Poe file
    parser.add_argument("poe", metavar="POE",
                        help="Enter a valid Poe file")
    # Argument for New Por file
    parser.add_argument("por", metavar="POR",
                        help="Enter a valid Por file")
    # Argument for Node annotation Poe file
    parser.add_argument("node", metavar="node",
                        help="Enter a valid Node annotation file")
    args = parser.parse_args()
    modelfile = args.m2
    poefile = args.poe
    porfile = args.por
    annot_nodes = args.node
    return modelfile, poefile, porfile, annot_nodes


def list_all_rules(modelfile):
    """
    As in the other program, this function creates a dictionary containing
    the rules and the weights of the model2 file.
    Returns :
        - The rule dictionary
    """
    dict_rules = {}
    index = 0
    with open(modelfile, 'r') as model_new:
        current_line = model_new.readline()
        while current_line != '':
            if current_line.rstrip() == "--INITIAL":
                break
            if current_line[0] != '%' and current_line != '\n':
                num_rule = 'R' + str(index)
                dict_rules[num_rule] = current_line.rstrip().split("\t")
                index += 1
            current_line = model_new.readline()
    return dict_rules


def find_used_rules(porfile):
    """
    This function uses the Por file to find all the rules that have been used
    during the simulation.
    It also computes the number of times each one has been used.
    Returns :
        - used_rules : A list of the used rules for each timestep.
        - nb_events : A dictionary that contains a list of the timesteps of
          the simulation and the number of events that occurred in each
          timestep
    """
    used_rules = []
    # Creating the dictionary of events from the porfile
    nb_events = {"Timestep":[], "Nb_events":[]}
    with open(porfile, 'r') as por:
        por_data = [[data for data in line.rstrip().split('\t')] \
                    for line in por]
    for timestep in por_data[1:]:
        nb_events["Timestep"].append(timestep[0])
        nb_events["Nb_events"].append(int(float(timestep[1])))
    # From the por file, it is possible to know every rule used in each
    # timestep
    for rule in range(2, len(por_data[0])):
    # We check for variations throughout the simulation, which shows the use
    # of a given rule
        if all(timestep[rule] == '0.000000' for timestep in por_data[1:]):
            pass
        elif all(timestep[rule] == '100.000000' for timestep in por_data[1:]):
            pass
        else:
            tmp_list = []
            for timestep in por_data[0:]:
                tmp_list.append(timestep[rule])
            used_rules.append(tmp_list)
    return used_rules, nb_events


def rules_in_timesteps(used_rules, nb_events):
    """
    This function creates a file that shows the rules used in each timestep
    of the simulation from the previous function
    File generated :
        - rules_applied.txt : In each timestep, the rules used by the
          simulation.
    """
    with open("./results/rules_applied.txt", "w") as rules_file:
        for step in range(0, len(nb_events["Timestep"])):
            tmp_rule_list = []
            tmp_nb_used_rule = []
            for used_rule in used_rules:
                if used_rule[step+1] != "0.000000":
                    tmp_rule_list.append(used_rule[0])
                    tmp_nb_used_rule.append(round(float(used_rule[step+1]) \
                        *nb_events["Nb_events"][step])/100)
            rules_file.write(textwrap.fill("At " + str(nb_events["Timestep"] \
                    [step]) + ", the rule(s) " + ", ".join(tmp_rule_list) + \
                    " has or have been used " + \
                    ", ".join(str(int(x)) for x in tmp_nb_used_rule) + \
                    " times respectively", width=80) + "\n")


def sim_possible_rules(dict_rules, poefile):
    """
    This functions computes the possible rules to be used in each step of the
    simulation from the poefile.
    It also gather the missing elements in each timestep and store them in
    a file.
    It creates another file containing the computed possible rules.
    Returns :
        - missing_elements : A list of the missing elements in the last
          timestep.
    Files generated :
        - lost_reactives.txt : A file containing the missing elements in each
          timestep.
        - possible_rules.txt : A file containing the possible rules to be used
          in each timestep.
    """
    reactives = []
    dict_possible_time = {}
    # Computes the reactives from the rule dictionary to compare with the
    # possible elements in each timestep.
    for rule in dict_rules:
        reactives.append(list(map(str.strip, \
            dict_rules[rule][0].split(sep='=>')[0].split(sep=' + '))))
    with open(poefile, 'r') as poe:
        poe_data = [[data for data in line.rstrip().split('\t')] \
        for line in poe]
    possible_elements = {"0.000000":[100]*(len(poe_data[0])-2)}
    title = 0
    for elt in poe_data[0:]:
        tmp_list = []
        if title == 0:
            possible_elements["Elements"] = elt[2:]
            title = 1
        else:
            tmp_list = elt[2:]
            for index, value in enumerate(tmp_list):
                if value == "0.000000":
                    tmp_list[index] = 0
                elif value == "100.000000":
                    tmp_list[index] = 100
                else:
                    tmp_list[index] = float(tmp_list[index])
            possible_elements[str(elt[0])] = tmp_list
    list_index = list(possible_elements.keys())
    list_index.remove("Elements")
    dict_possible_rules = {}
    # Computes the missing elements in each time step and add them in the
    # summary file.
    lost_reactives = open("./results/lost_reactives.txt", "w")
    for timestep in list_index:
        time_possible_elements_values = []
        time_possible_elements_keys = []
        missing_elements = []
        for i in range(0, len(possible_elements[timestep])):
            if possible_elements[timestep][i] != 0:
                time_possible_elements_keys.append(possible_elements["Elements"][i])
                time_possible_elements_values.append(possible_elements[timestep][i])
            else:
                missing_elements.append(possible_elements["Elements"][i])
        lost_reactives.write("Timestep : " + timestep + ", missing elements : \n")
        lost_reactives.write(str(missing_elements) + "\n")
        index = 0
        for reactivelist in reactives:
            rule_possible = True
            for reac in reactivelist:
                if reac not in time_possible_elements_keys:
                    rule_possible = False
            if rule_possible:
                rule = "R" + str(index)
                dict_possible_rules[rule] = dict_rules[rule]
            index += 1
        dict_possible_time[timestep] = dict.copy(dict_possible_rules)
        dict_possible_rules.clear()
    lost_reactives.close()
    # Creates the file containing the possible rules in each timestep.
    with open("./results/possible_rules.txt", "w") as possible_file:
        for dict_possible_rule in dict_possible_time:
            possible_file.write("Timestep : " + dict_possible_rule + "\n")
            possible_file.write(textwrap.fill(str(dict_possible_time \
                                [dict_possible_rule].keys()), width=80) \
                                + "\n")
    return missing_elements


def summary_missing_elements(missing_elements, annot_nodes):
    """
    This function creates a file similar to the edge annotation file containing
    only the information on the missing elements in the last timestep of the
    simulation. It allows the user to understand what are the last problems in
    the simulation.
    The following data is displayed for every element :
        - Element : The name of the element
        - Nreac : The number of times the element is a reactive in a rule
        - Nprod : The number of times the element is a product in a rule
        - Ratio : The ratio Nreac/Nprod
    File generated :
        - missing_elts_summary.txt : The file summarizing the missing elements
          in the last timestep of the simulation.
    """
    missing_elts_file = open("./results/missing_elts_summary.txt", "w")
    missing_elts_file.write("Element,Nreac,Nprod,Ratio\n")
    with open(annot_nodes, 'r') as elts_file:
        current_line = elts_file.readline()
        while current_line != "":
            line_as_list = current_line.split(",")
            if line_as_list[0] in missing_elements:
                missing_elts_file.write(current_line)
            current_line = elts_file.readline()


def main():
    """
    Main function of the program. Executes all the other defined functions.
    """
    modelfile, poefile, porfile, annot_nodes = args_parse()
    dict_rules = list_all_rules(modelfile)
    used_rules, nb_events = find_used_rules(porfile)
    rules_in_timesteps(used_rules, nb_events)
    missing_elements = sim_possible_rules(dict_rules, poefile)
    summary_missing_elements(missing_elements, annot_nodes)

if __name__ == "__main__":
    main()
