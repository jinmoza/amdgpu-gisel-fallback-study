
define amdgpu_kernel void @atomic_umin_ret_gds() {
  %val = atomicrmw umin ptr addrspace(2) null, i32 0 monotonic, align 4
  ret void
}
