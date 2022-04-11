# import numpy as np
# from sklearn.base import is_classifier
# from sklearn.tree import _tree, DecisionTreeClassifier
# from sklearn.tree._export import _compute_depth
# from sklearn.utils.validation import check_is_fitted
#
#
# def export_text(
#     decision_tree,
#     *,
#     feature_names=None,
#     max_depth=10,
#     spacing=3,
#     decimals=2,
#     show_weights=False,
# ):
#
#     check_is_fitted(decision_tree)
#     tree_ = decision_tree.tree_
#     if is_classifier(decision_tree):
#         class_names = decision_tree.classes_
#     right_child_fmt = "{} {} <= {}\n"
#     left_child_fmt = "{} {} >  {}\n"
#     truncation_fmt = "{} {}\n"
#
#     if max_depth < 0:
#         raise ValueError("max_depth bust be >= 0, given %d" % max_depth)
#
#     if feature_names is not None and len(feature_names) != tree_.n_features:
#         raise ValueError(
#             "feature_names must contain %d elements, got %d"
#             % (tree_.n_features, len(feature_names))
#         )
#
#     if spacing <= 0:
#         raise ValueError("spacing must be > 0, given %d" % spacing)
#
#     if decimals < 0:
#         raise ValueError("decimals must be >= 0, given %d" % decimals)
#
#     if isinstance(decision_tree, DecisionTreeClassifier):
#         value_fmt = "{}{} weights: {}\n"
#         if not show_weights:
#             value_fmt = "{}{}{}\n"
#     else:
#         value_fmt = "{}{} value: {}\n"
#
#     if feature_names:
#         feature_names_ = [
#             feature_names[i] if i != _tree.TREE_UNDEFINED else None
#             for i in tree_.feature
#         ]
#     else:
#         feature_names_ = ["feature_{}".format(i) for i in tree_.feature]
#
#     export_text.report = ""
#
#     def _add_leaf(value, class_name, indent):
#         val = ""
#         is_classification = isinstance(decision_tree, DecisionTreeClassifier)
#         if show_weights or not is_classification:
#             val = ["{1:.{0}f}, ".format(decimals, v) for v in value]
#             val = "[" + "".join(val)[:-2] + "]"
#         if is_classification:
#             val += " class: " + str(class_name)
#         export_text.report += value_fmt.format(indent, "", val)
#
#     def print_tree_recurse(node, depth):
#         indent = ("|" + (" " * spacing)) * depth
#         indent = indent[:-spacing] + "-" * spacing
#
#         value = None
#         if tree_.n_outputs == 1:
#             value = tree_.value[node][0]
#         else:
#             value = tree_.value[node].T[0]
#         class_name = np.argmax(value)
#
#         if tree_.n_classes[0] != 1 and tree_.n_outputs == 1:
#             class_name = class_names[class_name]
#
#         if depth <= max_depth + 1:
#             info_fmt = ""
#             info_fmt_left = info_fmt
#             info_fmt_right = info_fmt
#
#             if tree_.feature[node] != _tree.TREE_UNDEFINED:
#                 name = feature_names_[node]
#                 threshold = tree_.threshold[node]
#                 threshold = "{1:.{0}f}".format(decimals, threshold)
#                 export_text.report += right_child_fmt.format(indent, name, threshold)
#                 export_text.report += info_fmt_left
#                 print_tree_recurse(tree_.children_left[node], depth + 1)
#
#                 export_text.report += left_child_fmt.format(indent, name, threshold)
#                 export_text.report += info_fmt_right
#                 print_tree_recurse(tree_.children_right[node], depth + 1)
#             else:  # leaf
#                 _add_leaf(value, class_name, indent)
#         else:
#             subtree_depth = _compute_depth(tree_, node)
#             if subtree_depth == 1:
#                 _add_leaf(value, class_name, indent)
#             else:
#                 trunc_report = "truncated branch of depth %d" % subtree_depth
#                 export_text.report += truncation_fmt.format(indent, trunc_report)
#
#     print_tree_recurse(0, 1)
#     return export_text.report
