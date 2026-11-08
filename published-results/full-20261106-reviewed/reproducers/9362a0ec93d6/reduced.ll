
define i64 @load_i64_align4(ptr addrspace(2) %ptr) {
  %val = load i64, ptr addrspace(2) %ptr, align 4
  ret i64 %val
}
