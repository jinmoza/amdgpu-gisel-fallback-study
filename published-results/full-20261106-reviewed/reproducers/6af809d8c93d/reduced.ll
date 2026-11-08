
define amdgpu_kernel void @store_as4_2xi32() {
  store <2 x i32> zeroinitializer, ptr addrspace(4) null, align 8
  ret void
}
