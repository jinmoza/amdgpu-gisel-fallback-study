
define amdgpu_kernel void @store_as4_2xfloat() {
  store <2 x float> zeroinitializer, ptr addrspace(4) null, align 8
  ret void
}
