
define amdgpu_kernel void @store_as4_half() {
  store half 0.000000e+00, ptr addrspace(4) null, align 2
  ret void
}
