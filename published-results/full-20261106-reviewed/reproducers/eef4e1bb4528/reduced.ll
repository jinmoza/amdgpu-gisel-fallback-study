
define amdgpu_kernel void @atomic_umax_ret_gds() {
  %val = atomicrmw umax ptr addrspace(2) null, i32 0 monotonic, align 4
  ret void
}
