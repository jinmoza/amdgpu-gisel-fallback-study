
define amdgpu_kernel void @store_as4_double() {
  store double 0.000000e+00, ptr addrspace(4) null, align 8
  ret void
}
