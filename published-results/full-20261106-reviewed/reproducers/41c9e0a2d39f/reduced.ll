
define i32 @load_i32(ptr addrspace(2) %ptr) {
  %val = load i32, ptr addrspace(2) %ptr, align 4
  ret i32 %val
}
