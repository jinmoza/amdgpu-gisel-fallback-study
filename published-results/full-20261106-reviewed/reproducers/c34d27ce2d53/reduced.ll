
define amdgpu_kernel void @atomic_imin_ret_gds() {
  %val = atomicrmw min ptr addrspace(2) null, i32 0 monotonic, align 4
  ret void
}
