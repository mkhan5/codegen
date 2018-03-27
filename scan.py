import copy
import sys
import os
import re

from pycparser import c_parser
from pycparser import c_ast
sys.path.extend(['.', '..'])

from pycparser import parse_file, c_parser, c_generator
from pycparser import c_generator

from generator import Generator
class Scanner:
    def __init__(self):
        pass

    def gen_ast(self, flname):
        parser = c_parser.CParser()
        # ast = parser.parse(src)
        ast = parse_file(flname, use_cpp=True,
                 cpp_path='gcc',
                 cpp_args=['-E','-nostdinc',r'-Ipycparser/utils/fake_libc_include',r'-I/opt/intel/compilers_and_libraries_2016.1.150/linux/mkl/include','-I2mm/utilities'])
        return ast

    def wrap_c_code(self, text):
        newtext = "void func(){"+text+";}"
        return newtext

    def gen_ast_text(self, text):
        parser = c_parser.CParser()
        ast = parser.parse(text, filename='<none>')
        return ast

    def ignore_headers(self, filename, new_filename):
        input_data = [line.strip() for line in open(filename,'r')]
        mod_input_data = []
        for line in input_data:
            if not "#include" in line:
                mod_input_data.append(line);
        fp = open(new_filename, 'w')
        fp.writelines( "%s\n" % item for item in mod_input_data )
        fp.close()

    def show_func_calls(self, ast, funcname):
        v = FuncCallVisitor(funcname)
        v.visit(ast)

    def get_func_calls(self, ast, funcname):
        v = FuncCallVisitor(funcname)
        v.visit(ast)
        return v.nodelist

    def get_array_decls(self, ast):
        v = ArrayDeclVisitor()
        v.visit(ast)
        #return v.nodelist # returns only array names
        return v.ArrayDict #return array names and their size (dicitionary --> {tmpa : [3,5]}

    def get_ptr_decls(self, ast):
        v = PtrDeclVisitor()
        v.visit(ast)
        return v.nodelist


    def get_IDs(self, ast):
        v = IDVisitor()
        v.visit(ast)
        return v.nodelist

    def get_assignments(self, ast):
        v = AssignmentVisitor()
        v.visit(ast)
        return v.nodelist

    def print_c_code(self, ast):
        generator = c_generator.CGenerator()
        print(generator.visit(ast))

    def get_c_code(self, ast):
        generator = c_generator.CGenerator()
        return generator.visit(ast)

    def get_ptrAllocList(self,ast):
        ptrlist = self.get_ptr_decls(ast)
        assignlist = self.get_assignments(ast)
        ptrAllocDict = {}
        AllocDict = {}
        alloclist = []
        for asgn in assignlist:
            tmplist = []
            tmplist = self.get_func_calls(asgn, "mkl_malloc")
            if not (len(tmplist) == 0):
                if not (asgn.lvalue.name in alloclist):
                    str1 = ""
                    if type(tmplist[0].args.exprs[0]) is c_ast.BinaryOp:
                            str1 = self.get_c_code(tmplist[0].args.exprs[0])
                            str1 = re.sub('[*][ ]*\(sizeof\([a-zA-Z0-9]*\)\)', '', str1)
                            str1 = re.sub('\(sizeof\([a-zA-Z0-9]*\)\)[ ]*[*]', '', str1)
                            str1 = re.sub('[(]*', '', str1)
                            str1 = re.sub('[)]*', '', str1)
                            AllocDict[asgn.lvalue.name] = str1
                    alloclist.append(asgn.lvalue.name)
            tmplist = []
            tmplist = self.get_func_calls(asgn, "malloc")
            if not (len(tmplist) == 0):
                if not (asgn.lvalue.name in alloclist):
                    str1 = ""
                    if type(tmplist[0].args.exprs[0]) is c_ast.BinaryOp:
                            str1 = self.get_c_code(tmplist[0].args.exprs[0])
                            str1 = re.sub('[*][ ]*\(sizeof\([a-zA-Z0-9]*\)\)', '', str1)
                            str1 = re.sub('\(sizeof\([a-zA-Z0-9]*\)\)[ ]*[*]', '', str1)
                            str1 = re.sub('[(]*', '', str1)
                            str1 = re.sub('[)]*', '', str1)
                            AllocDict[asgn.lvalue.name] = str1
                    alloclist.append(asgn.lvalue.name)
            tmplist = []
            tmplist = self.get_func_calls(asgn, "realloc")
            if not (len(tmplist) == 0):
                if not (asgn.lvalue.name in alloclist):
                    str1 = ""
                    if type(tmplist[0].args.exprs[0]) is c_ast.BinaryOp:
                            str1 = self.get_c_code(tmplist[0].args.exprs[0])
                            str1 = re.sub('[*][ ]*\(sizeof\([a-zA-Z0-9]*\)\)', '', str1)
                            str1 = re.sub('\(sizeof\([a-zA-Z0-9]*\)\)[ ]*[*]', '', str1)
                            str1 = re.sub('[(]*', '', str1)
                            str1 = re.sub('[)]*', '', str1)
                            AllocDict[asgn.lvalue.name] = str1
                    alloclist.append(asgn.lvalue.name)
            tmplist = []
            tmplist = self.get_func_calls(asgn, "calloc")
            if not (len(tmplist) == 0):
                if not (asgn.lvalue.name in alloclist):
                    str1 = ""
                    if type(tmplist[0].args.exprs[0]) is c_ast.BinaryOp:
                            str1 = self.get_c_code(tmplist[0].args.exprs[0])
                            str1 = re.sub('[*][ ]*\(sizeof\([a-zA-Z0-9]*\)\)', '', str1)
                            str1 = re.sub('\(sizeof\([a-zA-Z0-9]*\)\)[ ]*[*]', '', str1)
                            str1 = re.sub('[(]*', '', str1)
                            str1 = re.sub('[)]*', '', str1)
                            AllocDict[asgn.lvalue.name] = str1
                    alloclist.append(asgn.lvalue.name)
        sa = set(alloclist)
        sb = set(ptrlist)
        ptrAllocList = sa.intersection(sb)
        for ptr in ptrAllocList:
            ptrAllocDict[ptr] = AllocDict[ptr]
        return ptrAllocDict



class FuncCallVisitor(c_ast.NodeVisitor):
    def __init__(self, funcname):
        self.funcname = funcname
        self.nodelist = []

    def visit_FuncCall(self, node):
        if node.name.name == self.funcname:
            self.nodelist.append(node)

class ArrayDeclVisitor(c_ast.NodeVisitor):
    def __init__(self):
        #self.funcname = funcname
        self.nodelist = []
        self.ArrayDict = {}


    def visit_ArrayDecl(self, node):
        if type(node) is c_ast.ArrayDecl:
            #1D Array

            if type(node.type) is c_ast.TypeDecl:
                if not (node.type.declname in self.nodelist):
                    self.nodelist.append(node.type.declname)
                    dim = []
                    dim.append(node.dim.value)
                    # "1d : ",node.dim.value
                    self.ArrayDict[node.type.declname] = dim

            #2D Array
            elif type(node.type) is c_ast.ArrayDecl:
                if not (node.type.type.declname in self.nodelist):
                    self.nodelist.append(node.type.type.declname)
                    #"2d 0: ",node.dim.value," 1: ",node.type.dim.value
                    dim = []
                    dim.append(node.dim.value)
                    dim.append(node.type.dim.value)
                    self.ArrayDict[node.type.type.declname] = dim


class PtrDeclVisitor(c_ast.NodeVisitor):
    def __init__(self):
        #self.funcname = funcname
        self.nodelist = []

    def visit_PtrDecl(self, node):
        if type(node.type) is c_ast.TypeDecl:
            if not (node.type.declname in self.nodelist):
                self.nodelist.append(node.type.declname)

class IDVisitor(c_ast.NodeVisitor):
    def __init__(self):
        #self.funcname = funcname
        self.nodelist = []

    def visit_ID(self, node):
        if type(node) is c_ast.ID:
            if not (node.name in self.nodelist):
                self.nodelist.append(node.name)

class AssignmentVisitor(c_ast.NodeVisitor):
    def __init__(self):
        #self.funcname = funcname
        self.nodelist = []

    def visit_Assignment(self, node):
        if type(node) is c_ast.Assignment:
            self.nodelist.append(node)


class LineReplace:
    def __init__(self):
        pass

    def replaceData(self, filename, start_lineno, end_lineno, text_from_file):
        self.filename = filename
        self.start_lineno = start_lineno
        self.end_lineno = end_lineno
        self.text_from_file = text_from_file

        input_data = [line.strip() for line in open(self.filename,'r')]
        replace_data = [line.strip() for line in open(self.text_from_file,'r')]
        input_data[start_lineno-1:end_lineno] = replace_data
        fp = open(filename, 'w')
        fp.writelines( "%s\n" % item for item in input_data )
        fp.close()

#replaces data from start_lineno to end_lineno (start_lineno, end_lineno inclusive)


if __name__ == "__main__":
    filename = os.getcwd()+'/gemv/gemv.c'
    new_filename = os.getcwd()+'/temp/temp.c'
    scanner = Scanner()
    scanner.ignore_headers(filename,new_filename)

    ast = scanner.gen_ast(new_filename)
    #ast.show()
    arraydict = scanner.get_array_decls(ast)
    ptrAllocDict = scanner.get_ptrAllocList(ast)

    print "Arrays ", list(arraydict.keys())
    print "Ptr Allocs ", ptrAllocDict
    nodelist = []
    nodelist = scanner.get_func_calls(ast, "cblas_dgemv")
    dev_vars = []
    cblas_args = []

    for node in nodelist:
        print node.name.name, node.name.coord
        #node.args.show()
        for exp in node.args.exprs:
            if type(exp) is c_ast.ID:
                if (exp.name in list(arraydict.keys())) or (exp.name in list(ptrAllocDict.keys())):
                    if not (exp.name in dev_vars):
                        dev_vars.append(exp.name)
                cblas_args.append(exp.name)
            elif type(exp) is c_ast.Constant:
                cblas_args.append(exp.value)

    print dev_vars
    print cblas_args
    v_type = "double"
    v_row = "m"
    v_col = "n"
    gen = Generator()
    gen.prettyprint(dev_vars,v_type,v_row,v_col)

    print "-------------------------------------"
    for line in gen.filelines:
        print line

    """
    #### TODO ####:
    Use the following file for MAP and cuda-->mkl functionality
     ~/PycharmProjects/migration/src/cblas_openblas.py

    add functionality to cut headers and later store those headers in the target file
    Priority --1. Replace, 2. Delete from Bottom (no prob with line index).
    #### END TODO ####
    """

    """
    cublasStatus_t status;
    cublasHandle_t handle;
    double *d_A = 0;
    double *d_x = 0;
    double *d_y = 0;

    cublasCreate(&handle);
    cudaMalloc((void **)&d_A, n * n * sizeof(d_A[0]));
    cudaMalloc((void **)&d_x,  n * sizeof(d_x[0]));
    cudaMalloc((void **)&d_y,  n * sizeof(d_y[0]));

    cudaMemcpy(d_A, A,  n * n * sizeof(double), cudaMemcpyHostToDevice);
    cudaMemcpy(d_x, x, n * sizeof(double), cudaMemcpyHostToDevice);

    cublasDgemv(handle       , CUBLAS_OP_T , n, n, &alpha, d_A, n, d_x, 1, &beta, d_y, 1);
  --cblas_dgemv(CblasRowMajor, CblasNoTrans, n, n, alpha,  A  , n,  x , 1, beta ,  w , 1);
    cudaMemcpy( w, d_y, n*sizeof(double), cudaMemcpyDeviceToHost);
    cudaFree(d_A);
    cudaFree(d_x);
    cudaFree(d_y);
    cublasDestroy(handle);"""
