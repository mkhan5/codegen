class Generator:
    def __init__(self):
        self.sc = ";"
        self.nl = "\n"
        self.dev = "d_"
        self.status = "dev_status"
        self.handle = "dev_handle"
        self.filelines = []

    def mem_alloc_mkl(self,var_name,var_type,var_row,var_col):
        alloc_str = var_type+" *"+var_name+self.sc+self.nl+var_name+" = ("+var_type+"*)mkl_malloc( "+var_row+"*"+var_col+"*sizeof( "+var_type+" ), 64 )"+self.sc
        print alloc_str

    def mem_dealloc_mkl(self,var_name):
        dealloc_str = "mkl_free("+var_name+")"+self.sc
        print dealloc_str

    def mem_alloc(self,var_name,var_type,var_row,var_col):
        alloc_str = var_type+" *"+var_name+self.sc+self.nl+var_name+" = ("+var_type+"*)malloc( "+var_row+"*"+var_col+"*sizeof( "+var_type+" ))"+self.sc
        print alloc_str

    def dev_var_dec(self,var_name,var_type):
        dev_var = self.dev+var_name
        alloc_str = var_type+" *"+dev_var+self.sc
        print alloc_str
        self.filelines.append(alloc_str)

    def dev_mem_alloc(self,var_name,var_type,var_row,var_col):
        dev_var = self.dev+var_name
        alloc_str = "cudaMalloc((void **)&"+dev_var+", "+var_row+"*"+var_col+"*sizeof( "+var_type+" ))"+self.sc
        print alloc_str
        self.filelines.append(alloc_str)

    def host_to_dev_mem_copy(self,var_name,var_type,var_row,var_col):
        dev_var = self.dev+var_name
        alloc_str = "cudaMemcpy("+dev_var +", "+var_name+", "+var_row+"*"+var_col+"*sizeof( "+var_type+" ),cudaMemcpyHostToDevice)"+self.sc
        print alloc_str
        self.filelines.append(alloc_str)

    def dev_to_host_mem_copy(self,var_name,var_type,var_row,var_col):
        dev_var = self.dev+var_name
        alloc_str = "cudaMemcpy("+var_name +", "+dev_var+", "+var_row+"*"+var_col+"*sizeof( "+var_type+" ),cudaMemcpyDeviceToHost)"+self.sc
        print alloc_str

    def dev_mem_dealloc(self,var_name):
        dev_var = self.dev+var_name
        dealloc_str = "cuda_free("+dev_var+")"+self.sc
        print dealloc_str
        self.filelines.append(dealloc_str)


    def mem_dealloc(self,var_name):
        dealloc_str = "free("+var_name+")"+self.sc
        print dealloc_str

    def dev_init(self,status,handle):
        dev_init1 = "cublasStatus_t "+status+self.sc
        dev_init2 = "cublasHandle_t "+handle+self.sc
        dev_init3 = "cublasCreate(&"+handle+")"+self.sc
        print dev_init1
        print dev_init2
        print dev_init3
        self.filelines.append(dev_init1)
        self.filelines.append(dev_init2)
        self.filelines.append(dev_init3)


    def dev_destroy(self,handle):
        destroy = "cublasDestroy("+handle+")"+self.sc
        print destroy
        self.filelines.append(destroy)

    def prettyprint(self,dev_vars,v_type,v_row,v_col):
        self.dev_init(self.status,self.handle)
        for dev_var in dev_vars:
            self.dev_var_dec(dev_var,v_type)
        for dev_var in dev_vars:
            self.dev_mem_alloc(dev_var,v_type,v_row,v_col)
        for dev_var in dev_vars:
            self.host_to_dev_mem_copy(dev_var,v_type,v_row,v_col)

        print " ----------cublasDgemv(handle       , CUBLAS_OP_T , n, n, &alpha, d_A, n, d_x, 1, &beta, d_y, 1); "
        print " ----------cudaMemcpy( w, d_y, n*sizeof(double), cudaMemcpyDeviceToHost); "

        for dev_var in dev_vars:
            self.dev_mem_dealloc(dev_var)
        self.dev_destroy(self.handle)


"""Code Testing From Here """
if __name__ == "__main__":
    v_name = "A"
    v_name2 = "B"
    v_name3 = "C"
    v_type = "double"
    v_row = "m"
    v_col = "n"
    g = Generator()
    g.dev_init(g.status,g.handle)
    g.mem_alloc_mkl(v_name,v_type,v_row,v_col)
    g.mem_alloc_mkl(v_name2,v_type,v_row,v_col)
    g.mem_alloc_mkl(v_name3,v_type,v_row,v_col)
    print( " .... ")
    g.dev_var_dec(v_name,v_type)
    g.dev_mem_alloc(v_name,v_type,v_row,v_col)


    g.host_to_dev_mem_copy(v_name,v_type,v_row,v_col)
    g.dev_to_host_mem_copy(v_name,v_type,v_row,v_col)

    g.dev_mem_dealloc(v_name)
    g.dev_destroy(g.handle)
    g.mem_dealloc(v_name)

    g.mem_dealloc_mkl(v_name)
    g.mem_dealloc_mkl(v_name2)
    g.mem_dealloc_mkl(v_name3)
