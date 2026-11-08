
define amdgpu_kernel void @store_as4_i8() {
  store i8 0, ptr addrspace(4) null, align 1
  ret void
}
