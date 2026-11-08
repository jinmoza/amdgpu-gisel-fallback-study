
define amdgpu_kernel void @store_as4_i16() {
  store i16 0, ptr addrspace(4) null, align 2
  ret void
}
