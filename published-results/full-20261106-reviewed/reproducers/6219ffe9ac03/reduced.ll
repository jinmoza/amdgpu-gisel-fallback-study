target datalayout = "m:e-G1-ni:7:8:9-p7:160:256:256:32-p8:128:128:128:48-p9:192:256:256:32-p10:32:32-p11:32:32-p12:32:32-p13:32:32-p14:32:32-p15:32:32"
target triple = "amdgpu9.00--"

define ptr addrspace(7) @sum_new_buffer_on_negative(ptr addrspace(7) %start, ptr addrspace(7) %start2, i1 %hop) {
entry:
  %ptr = select i1 %hop, ptr addrspace(7) %start, ptr addrspace(7) %start2
  ret ptr addrspace(7) %ptr
}
