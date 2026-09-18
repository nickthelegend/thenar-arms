#pragma once
#include <math.h>
#include <stdint.h>
namespace model {
constexpr float home[6]={0,-25,35,0,0,20};
constexpr float lo[6]={-85,-80,-80,-80,-85,0};
constexpr float hi[6]={85,80,80,80,85,70};
inline float wrappedDegrees(uint16_t raw,uint16_t zero){return (((int(raw)-int(zero)+2048)&4095)-2048)*360.f/4096;}
inline bool valid(const float *q){for(int i=0;i<6;i++)if(!isfinite(q[i])||q[i]<lo[i]||q[i]>hi[i])return false;return true;}
inline bool stale(uint32_t now,uint32_t last){return uint32_t(now-last)>250;}
inline float slew(float a,float b){return a+fmaxf(-.2f,fminf(.2f,b-a));}
// Direct drive. Servo zero (not the displayed home pose) is indexed at 1500 us.
inline float pulse(float q,float zero,float usPerDegree,int sign){return zero+q*usPerDegree*sign;}
}
