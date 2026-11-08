
define i32 @zextload_i8(ptr addrspace(2) %ptr) {
  %val = load i8, ptr addrspace(2) %ptr, align 1
  %ext = zext i8 %val to i32
  ret i32 %ext
}
