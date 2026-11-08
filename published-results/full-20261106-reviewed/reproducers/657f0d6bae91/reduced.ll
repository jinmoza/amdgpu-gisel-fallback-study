
define amdgpu_kernel void @atomic_add_ret_gds() {
  %val = atomicrmw add ptr addrspace(2) null, i32 0 monotonic, align 4
  ret void
}
