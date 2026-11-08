
define amdgpu_kernel void @lds_atomic_xchg_ret_pointer_offset() {
  %result = atomicrmw xchg ptr addrspace(3) null, ptr null monotonic, align 8
  ret void
}
