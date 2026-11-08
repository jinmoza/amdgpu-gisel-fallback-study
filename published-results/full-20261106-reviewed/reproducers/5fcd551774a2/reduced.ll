
define amdgpu_kernel void @trunc_store_v8i64_v8i16(<8 x i64> %in) {
entry:
  %trunc = trunc <8 x i64> %in to <8 x i16>
  store <8 x i16> %trunc, ptr addrspace(1) null, align 16
  ret void
}
