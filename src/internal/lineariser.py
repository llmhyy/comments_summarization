from nltk.parse import corenlp
from nltk.tree import Tree
import re


class Lineariser:

    def __init__(self):
        self.PARSER = corenlp.CoreNLPParser(url='http://localhost:9000')
        print("Warning: Make sure to start Stanford CoreNLP server before calling this "
              "module's functions")

    def get_parsetree(self, sent):
        """
        Return parse tree from sentence.

        :param sent: a string representing a sentence.
        :returns: nltk.tree.Tree.
        """
        parsed = self.PARSER.raw_parse(sent)
        collected = []
        for i in parsed:
            collected.append(i)
        parsetree = collected[0]
        return parsetree

    def get_child_labels(self, t: Tree):
        """
        :param t: an nltk.tree.Tree
        :returns: list of labels of the children.
        """
        labels = []
        for child in t:
            labels.append(child.label())

        return labels

    def find_sub(self, t: Tree):
        """
        Recursively finds words/phrases (refer to them as 'components') that are joined by a 'CC' symbol and that
        describe a subject.

        :param t: an nltk.tree.Tree
        :returns: list of nltk.tree.Tree
        """
        # recursion ends once 'CC' symbol is found or leaves are reached.

        subtrees = []

        if t.height() > 2:
            # if tree height == 2, we only have leaves (string type) left in the tree.
            child_labels = self.get_child_labels(t)
            try:
                cc_index = child_labels.index('CC')
            except ValueError:
                cc_index = None
            if cc_index:
                if t[cc_index].leaves()[0].lower() not in ['or', 'nor']:
                    subtrees.append(t)
            else:
                for child in t:
                    if type(child) == Tree:
                        if child.label() != 'SBAR':
                            # can't remember what this condition is for.
                            result = self.find_sub(child)  # recurse deeper.
                            subtrees.extend(result)  # accumulate results.

        return subtrees

    def clean_comma(self, s):
        # recursion because it is unknown how many ' ,' substrings there might be.
        idx = s.find(' ,')
        if idx > -1:
            s = s[:idx] + s[idx + 1:]
            s = self.clean_comma(s)
        return s

    def clean_sent(self, s):
        """
        Helper function. Removes whitespace before period '.' tokens and ',' tokens.
        """
        if len(s) > 2:
            if s[-2:] == ' .':
                s = s[:-2] + '.'

        s = self.clean_comma(s)
        return s

    def linearise(self, s):
        """
        From a sentence, generates constituent sentences describing the same subject, if they exist.

            e.g. "You grasp concepts easily and may become impatient with those who don't learn as quickly."
            can be broken down into "You grasp concepts easily" and "You may become impatient with those who don't learn as quickly."

        Looks for parallel noun phrases (NP, NN), parallel verbs (VP, V) and parallel adjectives (ADJP, JJ).
        Parallel phrases means these phrases are children of the same node, joined by some CC.
        Also takes parallel sentences (S) into account.
        Also takes conditions ("if" or SBAR) into account.
        Does not linearize around 'or' and 'nor' CCs (to be improved in later verions)

        We use a recursive approach to find the parallel parts once it finds the first
        VP co-occuring (parallel) with an NP.

        Sentences are then reconstructed by preserving the order in which phrases appear.

        :param s: a string representing a sentence.
        :returns: list of simpler sentences (strings), or None if no smaller sentences are found.
        :exceptions: raised when an unsupported structure is detected.
        """
        t = self.get_parsetree(s)[0]

        components = []  # todo: find a better/more intuitive name for components.
        left = None
        right = None

        final_sents = []

        labels = self.get_child_labels(t)

        #     for child in t:
        #         if child.label() == 'SBAR':
        #             #print('precondition found.')
        #             preconditions.extend(child.leaves())

        if labels.count('S') >= 2:
            # print(">=2 'S' found on same level.")
            for child in t:
                if child.label() == 'S':
                    components.append(child.leaves())
            # print('new sentences are :')
            for sent in components:
                final_sent_arr = []
                final_sent_arr.extend(sent)
                final_sent = " ".join(final_sent_arr) + '.'
                final_sents.append(final_sent)
            return final_sents

        elif 'NP' in labels:
            np_label = labels.index('NP')

            if 'VP' in labels:
                vp_index = labels.index('VP')
                labels2 = self.get_child_labels(t[vp_index])

                # check if 'CC' exists; todo: refactor?.
                leaves_POS = t[vp_index].pos()
                cc_exists = False
                for pair in leaves_POS:
                    if pair[1] in ['CC']:
                        cc_exists = True
                        break

                if cc_exists:
                    # find words/phrases joined by 'CC'.
                    sub_trees = self.find_sub(t[vp_index])  # recursive step.
                    if len(sub_trees) > 1:
                        print('no. of subtrees found: ', len(sub_trees))
                        raise Exception('Sentence structure not supported.')
                    if len(sub_trees) == 0:
                        return None
                    components_tree = sub_trees[0]
                    # find phrases to the left and right of the components group.
                    original_sent_arr = t.leaves()
                    original_sent = " ".join(
                        original_sent_arr)  # doesn't deal with punctuation tokens well, e.g. ','.
                    components_phrase_arr = components_tree.leaves()
                    components_phrase = " ".join(components_phrase_arr)
                    comp_index = original_sent.find(components_phrase)
                    left = original_sent[:comp_index].strip()
                    right = original_sent[comp_index + len(components_phrase):].strip()
                    # print('left ', left)
                    # print(components_phrase)
                    # print('right ', right)
                    
                    # find NN-like symbols, e.g. NP, NNS.
                    children_labels = []
                    for child in components_tree:
                        children_labels.append(child.label())
                        r = re.compile("N\D*")
                        search_result = list(filter(r.match, children_labels))
                     
                    if len(search_result) == 1:  # only one NN-like found
                        if children_labels[-1] in search_result: # likely the case of "a JJ and JJ NP."
                            # append components_tree[-1] phrase to start of 'right' phrase.
                            new = " ".join(components_tree[-1].leaves())
                            right = new + " " + right
                            # add all but tree[-1] to components list:
                            for child in components_tree[:-1]:
                                if child.label() in ['ADJP', 'JJ', 'VP', 'VB', 'NP', 'NN', 'NNS', 'NNP', 'NNPS']:
                                    components.append(child.leaves())
                    else:    
                        for child in components_tree:
                            if child.label() in ['ADJP', 'JJ', 'VP', 'VB', 'NP', 'NN', 'NNS', 'NNP', 'NNPS']:
                                components.append(child.leaves())

                    # find adverbs if they exist, and preserve ordering.
                    # this is for the particular case of adverb co-occuring with conjunct phrases.
                    # e.g. You are the [MOST wonderful and capable] captain the world has ever seen.
                    # it is assumed that this modifier occurs at extreme left or right of components group.
                    components_list = list(components_tree)
                    premodifier = None
                    postmodifier = None
                    if components_list[0].label() in ['RB', 'RBR', 'RBS']:
                        premodifier = components_list[0].leaves()
                    if components_list[-1].label() in ['RB', 'RBR', 'RBS']:
                        postmodifier = components_list[-1].leaves()
                    if premodifier:
                        premodifier_str = " ".join(premodifier)
                        left = left + ' ' + premodifier_str
                    if postmodifier:
                        postmodifier_str = " ".join(postmodifier)
                        right = postmodifier_str + ' ' + right

                        # construct new sentences
                    for leaf in components:
                        mid = " ".join(leaf).strip()
                        final_sent = left + ' ' + mid + ' ' + right
                        final_sent = self.clean_sent(final_sent)  # remove unwanted
                        # whitespace.
                        final_sents.append(final_sent)
                    return final_sents
        else:
            print("Warning: Sentence structure not covered by function.")
        return None