"""
This module allows the user to modify a .model2 file, changing its weights
given an arbitrary set of rules based on the proportion of elements in
reactives and products. It also generates the files destined to a
cytoscape visualization.
"""
import argparse


def args_parse():
    """
    Parses the given arguments when function is called.
        - Original Model2 file
        - Original Poe file
    Returns :
        - The two mandatory arguments as variables modelfile and poefile
    """
    parser = argparse.ArgumentParser()
    # Argument for Original Model2 file
    parser.add_argument("m2", metavar="MODEL2",
                        help="Enter a valid model 2 file")
    # Argument for Original Poe file
    parser.add_argument("poe", metavar="POE", default=21,
                        help="Enter a valid Poe file")

    args = parser.parse_args()
    modelfile = args.m2
    poefile = args.poe
    return modelfile, poefile


def list_all_rules(modelfile):
    """
    This function takes the given model2 file and creates a dictionary
    containing all the model rules. The keys are the rule numbers and the
    values are lists containing the associated rules and their weights.
    It also creates the cytoscape file containing every interaction, protein
    to protein in all the rules, destined to generate a network.
    Returns :
        - dict_rules : The rule dictionary
        - network_inters : A dictionnary linked to the cytoscape network, that
          will be used later to create the edge annotation file
    File generated :
        - cytoscape_network.sif : A network file for Cytoscape.
    """
    dict_rules = {}
    index = 0
    cytosfile = open("./results/cytoscape_network.sif", "w")
    network_inters = {}
    with open(modelfile, 'r') as model2:
        current_line = model2.readline()
        while current_line != '':
            # Parsing the model2 file to create the dictionary
            if current_line.rstrip() == "--INITIAL":
                break
            if current_line[0] != '%' and current_line != '\n':
                num_rule = 'R' + str(index)
                dict_rules[num_rule] = current_line.rstrip().split("\t")
                network_inters[num_rule] = []
                index += 1
                #Creating cytoscape network
                for reac in current_line.rstrip().split("\t")[0]. \
                            split(sep='=>')[0].split(sep=' + '):
                    for prod in current_line.rstrip().split("\t")[0]. \
                            split(sep='=>')[1].split(sep=' + '):
                        to_network = reac.strip() + " pp " + prod.strip() + "\n"
                        to_edge_att = reac.strip() + " (pp) " + prod.strip()
                        network_inters[num_rule].append([to_edge_att,
                                                         current_line.rstrip() \
                                                         .split("\t")[1], 0.0])
                        cytosfile.write(to_network)
            current_line = model2.readline()
    return dict_rules, network_inters


def list_all_elts(poefile):
    """
    This functions creates a list that contains all unique elements in the
    model2 file. The poe file is used to ease the computation.
    Returns :
        - all_elts_list : A list that contains every element in the model.
    """
    with open(poefile, 'r') as poe:
        all_elts_list = poe.readline().strip().split(sep='\t')
    return all_elts_list

def make_list_reac_prod(dict_rules):
    """
    This function returns two lists, one containing every reactive in the model
    and one containing every product. Both will be used later to estimate
    better weights more easily
    Returns :
        - reac_list : A list of all the reactives in the model
        - prod_list : A list of all the products in the model
    """
    tmp_reac_list = []
    tmp_prod_list = []
    reac_list = []
    prod_list = []
    # Every rule in the rule dictionary is split between reactive and product
    for rule in dict_rules:
        tmp_reac_list.append(dict_rules[rule][0].split(sep='=>')[0] \
                            .split(sep=' + '))
        tmp_prod_list.append(dict_rules[rule][0].split(sep='=>')[1] \
                            .split(sep=' + '))
    # The program parses both sublists and splits reactives and products
    for lists_reac in tmp_reac_list:
        for reac in lists_reac:
            reac_list.append(reac.strip())
    for lists_prod in tmp_prod_list:
        for prod in lists_prod:
            prod_list.append(prod.strip())
    return reac_list, prod_list


def sugg_element(all_elts_list, reac_list, prod_list):
    """
    This function creates the node annotation file for the cytoscape network
    visualization. It contains :
        - Element : The name of the element
        - Nreac : The number of times the element is a reactive in a rule
        - Nprod : The number of times the element is a product in a rule
        - Ratio : The ratio Nreac/Nprod
    It creates the file on the fly.
    Returns :
        dict_sugg_elt : The dictionary corresponding to the generated file for 
        further use.
    File generated :
        annot_node.csv : A node annotation file for the Cytoscape network.
    """
    dict_sugg_elt = {'Element' : [],
                     'Nreac' : [],
                     'Nprod' : [],
                     'Ratio' : []
                    }
    # The annotation file is generated at the same time as the dictionary
    with open('./results/annot_node.csv', 'w') as outfile:
        outfile.write('Element,Nreac,Nprod,Ratio\n')
        for elt in all_elts_list[2:]:
            nb_reac = reac_list.count(elt)
            nb_prod = prod_list.count(elt)
            # Verifying the possibility to calculate the ratio. Otherwise value
            # is put to 0
            if nb_prod != 0 and nb_reac != 0:
                ratio = nb_reac/nb_prod
                strout = elt + ',' + str(nb_reac) + ',' \
                + str(nb_prod) + ',' + '{0:.3f}'.format(ratio)
                outfile.write(strout)
            elif nb_prod == 0 or nb_reac == 0:
                ratio = 0
                strout = elt + ',' + str(nb_reac) + ',' \
                + str(nb_prod) + ',' + '0'
                outfile.write(strout)
            # Checking if there are unused elements in the model
            elif nb_prod == 0 and nb_reac == 0:
                ratio = 0
                strout = elt + ' is never used in the simulation and \
                                can be removed'
                outfile.write(strout)
            dict_sugg_elt['Element'].append(elt)
            dict_sugg_elt['Nreac'].append(nb_reac)
            dict_sugg_elt['Nprod'].append(nb_prod)
            dict_sugg_elt['Ratio'].append(float('{0:.3f}'.format(ratio)))
            outfile.write('\n')
    return dict_sugg_elt


def rules_to_weigh(dict_rules, dict_sugg_elt):
    """
    This function computes the mean ratios for reactives and products
    separately for each rule. Every ratio calculated for an element is
    summed with the others in a given rule and the average is taken.
    Returns :
        dict_to_weigh : The dictionnary containing mean ratios for every rule.
    """
    dict_to_weigh = {}
    for rule in dict_rules:
        dict_to_weigh[rule] = [0, 0]
        reactives = dict_rules[rule][0].split(sep='=>')[0].split(sep=' + ')
        products = dict_rules[rule][0].split(sep='=>')[1].split(sep=' + ')
        mean_reac_ratio = 0
        mean_prod_ratio = 0
        for reac in reactives:
            mean_reac_ratio += dict_sugg_elt['Ratio'][dict_sugg_elt['Element']\
                                .index(reac.strip())]
        for prod in products:
            mean_prod_ratio += dict_sugg_elt['Ratio'][dict_sugg_elt['Element']\
                                .index(prod.strip())]
        dict_to_weigh[rule][0] = float(mean_reac_ratio/len(reactives))
        dict_to_weigh[rule][1] = float(mean_prod_ratio/len(products))
    return dict_to_weigh


def change_weight(dict_rules, dict_to_weigh, modelfile,
                  network_inters):
    """
    This function creates a new model2 file containing the updated ratios for
    every rule in the original model2 file. New ratios are calculated
    arbitrarily given several conditions (*4, *2, /4, /2) and can be modified
    It also computes edge and node annotation files for the cytoscape network
    representation.
    Files generated :
        - updated_modelfile.model2 : An updated model2 file with new weights.
        - annot_edge.csv : An edge annotation file for the Cytoscape network.
    """
    # For each rule, a new weight value is added given the values of reactive
    # and product mean ratios for each rule.
    for rule in dict_to_weigh:
        if dict_to_weigh[rule][0] > 1 and dict_to_weigh[rule][1] <= 1:
            dict_rules[rule][1] = float(dict_rules[rule][1])*4
        elif dict_to_weigh[rule][0] <= 1 and dict_to_weigh[rule][1] > 1:
            dict_rules[rule][1] = float(dict_rules[rule][1])/4
        elif dict_to_weigh[rule][0] < 1 and dict_to_weigh[rule][1] < 1 \
            and dict_to_weigh[rule][0] > dict_to_weigh[rule][1]:
            dict_rules[rule][1] = float(dict_rules[rule][1])*2
        elif dict_to_weigh[rule][0] < 1 and dict_to_weigh[rule][1] < 1 \
            and dict_to_weigh[rule][0] < dict_to_weigh[rule][1]:
            dict_rules[rule][1] = float(dict_rules[rule][1])/2
        elif dict_to_weigh[rule][0] > 1 and dict_to_weigh[rule][1] > 1 \
            and dict_to_weigh[rule][0] > dict_to_weigh[rule][1]:
            dict_rules[rule][1] = float(dict_rules[rule][1])/2
        elif dict_to_weigh[rule][0] > 1 and dict_to_weigh[rule][1] > 1 \
            and dict_to_weigh[rule][0] < dict_to_weigh[rule][1]:
            dict_rules[rule][1] = float(dict_rules[rule][1])*2
        # Values are updated in the future edge annotation file
        for interaction in network_inters[rule]:
            interaction[2] = dict_rules[rule][1]
    # The last rule of the model NONE => NONE is reset to 0.001
    dict_rules['R95'][1] = '0.001'
    # The model2 file is generated with new weigths and base on the original
    with open("./results/updated_modelfile.model2", 'w') as outfile:
        for rule in dict_rules:
            strout = dict_rules[rule][0] + '\t' \
                     + str(float(dict_rules[rule][1]))
            outfile.write(strout)
            outfile.write('\n')
        modelfile_old = open(modelfile, 'r')
        current_line = modelfile_old.readline().strip()
        cond = 0
        while current_line != '':
            if current_line == '--INITIAL':
                cond = 1
            if cond == 1:
                outfile.write(current_line)
                outfile.write('\n')
            current_line = modelfile_old.readline().strip()
        modelfile_old.close()
    # The edge annotation file is generated based on the informations collected
    # throughout the program.
    with open('./results/annot_edge.csv', 'w') as edgefile:
        edgefile.write('\t'.join(["Edge", "Score_init", "Score_changed"]) \
                        + "\n")
        for rule in network_inters:
            for interaction in network_inters[rule]:
                edgefile.write('\t'.join(map(str, interaction)) + "\n")


def main():
    """
    Main function of the program. Executes all the other defined functions.
    """
    modelfile, poefile = args_parse()
    dict_rules, network_inters = list_all_rules(modelfile)
    all_elts_list = list_all_elts(poefile)
    reac_list, prod_list = make_list_reac_prod(dict_rules)

    dict_sugg_elt = sugg_element(all_elts_list, reac_list, prod_list)
    dict_to_weigh = rules_to_weigh(dict_rules, dict_sugg_elt)

    change_weight(dict_rules, dict_to_weigh, modelfile,
                  network_inters)

if __name__ == "__main__":
    main()
