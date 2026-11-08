
define amdgpu_kernel void @store_as4_i64() {
  store i64 0, ptr addrspace(4) null, align 4
  ret void
}
