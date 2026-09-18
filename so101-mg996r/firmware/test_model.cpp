#include "thenar/model.h"
#include <cassert>
#include <cstdio>
int main(){
 assert(fabs(model::wrappedDegrees(2,4094)-.3515625f)<1e-6);
 assert(fabs(model::wrappedDegrees(4094,2)+.3515625f)<1e-6);
 assert(model::valid(model::home));float q[6]={0,-25,35,0,0,20};
 q[0]=NAN;assert(!model::valid(q));q[0]=86;assert(!model::valid(q));
 assert(model::stale(10,uint32_t(-300)));assert(!model::stale(10,uint32_t(-200)));
 assert(fabs(model::pulse(10,1500,5.5,1)-1555)<1e-6);
 assert(fabs(model::pulse(10,1500,5.5,-1)-1445)<1e-6);
 assert(fabs(model::slew(0,80)-.2)<1e-6);
 puts("PASS encoder wrap, limits, direct-drive pulse mapping, slew, watchdog rollover");
}
