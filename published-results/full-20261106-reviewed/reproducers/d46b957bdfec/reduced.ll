
define amdgpu_kernel void @atomic_imax_ret_gds() {
  %val = atomicrmw max ptr addrspace(2) null, i32 0 monotonic, align 4
  ret void
}
