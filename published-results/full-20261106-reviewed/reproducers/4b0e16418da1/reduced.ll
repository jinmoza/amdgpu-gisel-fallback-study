
define amdgpu_kernel void @uniform_or_i8(i8 %val) {
  %rmw = atomicrmw or ptr addrspace(1) null, i8 %val monotonic, align 1
  ret void
}
