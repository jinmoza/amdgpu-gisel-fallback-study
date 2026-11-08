
define amdgpu_kernel void @store_as4_2xhalf() {
  store <2 x half> zeroinitializer, ptr addrspace(4) null, align 4
  ret void
}
