
define amdgpu_kernel void @store_as4_2xi16() {
  store <2 x i16> zeroinitializer, ptr addrspace(4) null, align 4
  ret void
}
