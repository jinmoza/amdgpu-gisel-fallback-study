
define amdgpu_kernel void @atomic_xor_ret_gds() {
  %val = atomicrmw xor ptr addrspace(2) null, i32 0 monotonic, align 4
  ret void
}
