
define amdgpu_kernel void @alloca_9xi64_max1024() {
entry:
  %tmp = alloca [9 x i64], align 8, addrspace(5)
  %tmp2 = load i64, ptr addrspace(5) %tmp, align 4
  store i64 %tmp2, ptr addrspace(1) null, align 4
  ret void
}
