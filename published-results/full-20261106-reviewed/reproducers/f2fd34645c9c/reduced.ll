
define amdgpu_kernel void @store_as4_float() {
  store float 0.000000e+00, ptr addrspace(4) null, align 4
  ret void
}
