
define amdgpu_kernel void @phi_v7f64(i1 %cond) {
entry:
  br i1 %cond, label %then, label %finally

then:                                             ; preds = %entry
  br label %finally

finally:                                          ; preds = %then, %entry
  %val = phi <7 x double> [ splat (double 1.000000e+00), %then ], [ zeroinitializer, %entry ]
  store <7 x double> %val, ptr null, align 1
  ret void
}
