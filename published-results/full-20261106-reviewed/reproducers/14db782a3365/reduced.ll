
define amdgpu_kernel void @atomic_and_ret_gds() {
  %val = atomicrmw and ptr addrspace(2) null, i32 0 monotonic, align 4
  ret void
}
