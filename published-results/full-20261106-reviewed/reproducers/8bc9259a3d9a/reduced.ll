
define i32 @buffer_fat_ptr_agent_atomic_usub_sat_ret_u32__offset__amdgpu_no_fine_grained_memory() {
  %result = atomicrmw usub_sat ptr addrspace(7) null, i32 0 monotonic, align 4, !amdgpu.no.fine.grained.memory !0
  ret i32 %result
}

!0 = !{}
