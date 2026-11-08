
define amdgpu_kernel void @store_as4_2xdouble() {
  store <2 x double> zeroinitializer, ptr addrspace(4) null, align 16
  ret void
}
