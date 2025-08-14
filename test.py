# import ast

# code = """
# def greet(name):
#     print("Hello", name)
# """

# tree = ast.parse(code)
# print(ast.dump(tree, indent=4))


# # Module(
# #     body=[
# #         FunctionDef(
# #             name='greet',
# #             args=arguments(
# #                 args=[
# #                     arg(arg='name')]),
# #             body=[
# #                 Expr(
# #                     value=Call(
# #                         func=Name(id='print', ctx=Load()),
# #                         args=[
# #                             Constant(value='Hello'),
# #                             Name(id='name', ctx=Load())]))])])






import dis

def example():
    return sum([1, 2, 3])

dis.dis(example)
#  34           RESUME                   0

#  35           LOAD_GLOBAL              1 (sum + NULL)
#               BUILD_LIST               0
#               LOAD_CONST               1 ((1, 2, 3))
#               LIST_EXTEND              1
#               CALL                     1
#               RETURN_VALUE
