
define amdgpu_kernel void @kernel(i1 %tmp31.i) {
bb:
  br label %bb5

bb5:                                              ; preds = %bb33.i, %bb5, %bb
  %tmp4.i.sroa.0.0 = phi <9 x double> [ poison, %bb ], [ splat (double 1.000000e+00), %bb5 ], [ zeroinitializer, %bb33.i ]
  br i1 %tmp31.i, label %bb33.i, label %bb5

bb33.i:                                           ; preds = %bb5
  %tmp0 = extractelement <9 x double> %tmp4.i.sroa.0.0, i64 0
  store double %tmp0, ptr addrspace(1) null, align 8
  br label %bb5
}
