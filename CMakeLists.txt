PROJECT(ode)
cmake_minimum_required(VERSION 2.8)
include(../conanbuildinfo.cmake)
CONAN_BASIC_SETUP()

option(USE_DOUBLE_PRECISION "On for double precision, off for single precision" OFF)

set(Ode_SOURCES
	ode/src/array.cpp
	ode/src/box.cpp
	ode/src/capsule.cpp
	ode/src/collision_convex_trimesh.cpp
	ode/src/collision_cylinder_box.cpp
	ode/src/collision_cylinder_plane.cpp
	ode/src/collision_cylinder_sphere.cpp
	ode/src/collision_cylinder_trimesh.cpp
	ode/src/collision_kernel.cpp
	#ode/src/collision_libccd.cpp
	ode/src/collision_quadtreespace.cpp
	ode/src/collision_sapspace.cpp
	ode/src/collision_space.cpp
	ode/src/collision_transform.cpp
	ode/src/collision_trimesh_box.cpp
	ode/src/collision_trimesh_ccylinder.cpp
	ode/src/collision_trimesh_disabled.cpp
	ode/src/collision_trimesh_distance.cpp
	ode/src/collision_trimesh_gimpact.cpp
	ode/src/collision_trimesh_opcode.cpp
	ode/src/collision_trimesh_plane.cpp
	ode/src/collision_trimesh_ray.cpp
	ode/src/collision_trimesh_sphere.cpp
	ode/src/collision_trimesh_trimesh.cpp
	ode/src/collision_trimesh_trimesh_new.cpp
	ode/src/collision_util.cpp
	ode/src/convex.cpp
	ode/src/cylinder.cpp
	ode/src/error.cpp
	ode/src/export-dif.cpp
	ode/src/heightfield.cpp
	ode/src/joints/amotor.cpp
	ode/src/joints/ball.cpp
	ode/src/joints/contact.cpp
	ode/src/joints/dball.cpp
	ode/src/joints/dhinge.cpp
	ode/src/joints/fixed.cpp
	ode/src/joints/hinge.cpp
	ode/src/joints/hinge2.cpp
	ode/src/joints/joint.cpp
	ode/src/joints/lmotor.cpp
	ode/src/joints/null.cpp
	ode/src/joints/piston.cpp
	ode/src/joints/plane2d.cpp
	ode/src/joints/pr.cpp
	ode/src/joints/pu.cpp
	ode/src/joints/slider.cpp
	ode/src/joints/transmission.cpp
	ode/src/joints/universal.cpp
	ode/src/lcp.cpp
	ode/src/mass.cpp
	ode/src/mat.cpp
	ode/src/matrix.cpp
	ode/src/memory.cpp
	ode/src/misc.cpp
	ode/src/objects.cpp
	ode/src/obstack.cpp
	ode/src/ode.cpp
	ode/src/odeinit.cpp
	ode/src/odemath.cpp
	ode/src/odeou.cpp
	ode/src/odetls.cpp
	ode/src/plane.cpp
	ode/src/quickstep.cpp
	ode/src/ray.cpp
	ode/src/rotation.cpp
	ode/src/sphere.cpp
	ode/src/step.cpp
	ode/src/threading_base.cpp
	ode/src/threading_impl.cpp
	ode/src/threading_pool_posix.cpp
	ode/src/threading_pool_win.cpp
	ode/src/timer.cpp
	ode/src/util.cpp
	ode/src/fastdot.c
	ode/src/fastldlt.c
	ode/src/fastlsolve.c
	ode/src/fastltsolve.c
	ode/src/nextafterf.c
	OPCODE/Ice/IceAABB.cpp
	OPCODE/Ice/IceContainer.cpp
	OPCODE/Ice/IceHPoint.cpp
	OPCODE/Ice/IceIndexedTriangle.cpp
	OPCODE/Ice/IceMatrix3x3.cpp
	OPCODE/Ice/IceMatrix4x4.cpp
	OPCODE/Ice/IceOBB.cpp
	OPCODE/Ice/IcePlane.cpp
	OPCODE/Ice/IcePoint.cpp
	OPCODE/Ice/IceRandom.cpp
	OPCODE/Ice/IceRay.cpp
	OPCODE/Ice/IceRevisitedRadix.cpp
	OPCODE/Ice/IceSegment.cpp
	OPCODE/Ice/IceTriangle.cpp
	OPCODE/Ice/IceUtils.cpp
	OPCODE/Opcode.cpp
	OPCODE/OPC_AABBCollider.cpp
	OPCODE/OPC_AABBTree.cpp
	OPCODE/OPC_BaseModel.cpp
	OPCODE/OPC_Collider.cpp
	OPCODE/OPC_Common.cpp
	OPCODE/OPC_HybridModel.cpp
	OPCODE/OPC_LSSCollider.cpp
	OPCODE/OPC_MeshInterface.cpp
	OPCODE/OPC_Model.cpp
	OPCODE/OPC_OBBCollider.cpp
	OPCODE/OPC_OptimizedTree.cpp
	OPCODE/OPC_Picking.cpp
	OPCODE/OPC_PlanesCollider.cpp
	OPCODE/OPC_RayCollider.cpp
	OPCODE/OPC_SphereCollider.cpp
	OPCODE/OPC_TreeBuilders.cpp
	OPCODE/OPC_TreeCollider.cpp
	OPCODE/OPC_VolumeCollider.cpp
	ou/src/ou/atomic.cpp
	ou/src/ou/customization.cpp
	ou/src/ou/malloc.cpp
	ou/src/ou/threadlocalstorage.cpp)



include_directories(${CMAKE_SOURCE_DIR}/include)
include_directories(${CMAKE_SOURCE_DIR}/ode/src)
include_directories(${CMAKE_SOURCE_DIR}/ode/src/joints)
include_directories(${CMAKE_SOURCE_DIR}/OPCODE)
#include_directories(${CMAKE_SOURCE_DIR}/GIMPACT/include)
#include_directories(${CMAKE_SOURCE_DIR}/libccd/src)
include_directories(${CMAKE_SOURCE_DIR}/ou/include)

set(ODE_VERSION 0.14)
#set(CCD_PRECISION CCD_UNDEFINEDPRECISION)
if(USE_DOUBLE_PRECISION)
	add_definitions(-DdIDEDOUBLE -DCCD_IDEDOUBLE)
	set(ODE_PRECISION dDOUBLE)
	set(LIB_NAME ode_double)
else()
	add_definitions(-DdIDESINGLE -DCCD_IDESINGLE)
	set(ODE_PRECISION dSINGLE)
	set(LIB_NAME ode_single)
endif()
if(APPLE)
	add_definitions(-DMAC_OS_X_VERSION=1050)
	# Workaround to not display warnings about deprecated OSAtomic*
	set(CMAKE_C_FLAGS ${CMAKE_C_FLAGS} -Wno-deprecated)
	set(CMAKE_CXX_FLAGS ${CMAKE_CXX_FLAGS} -Wno-deprecated)
endif()
configure_file(include/ode/version.h.in include/ode/version.h)
configure_file(include/ode/precision.h.in include/ode/precision.h)
#configure_file(libccd/src/ccd/precision.h.in libccd/src/ccd/precision.h)

set(CMAKE_DEBUG_POSTFIX d)

if(BUILD_SHARED_LIBS)
	add_definitions(-DODE_DLL)
else()
	add_definitions(-DODE_LIB)
endif()
add_definitions(-D_USE_MATH_DEFINES -D_OU_NAMESPACE=odeou)
add_library(${LIB_NAME} ${Ode_SOURCES})

if(APPLE)
	set_target_properties(${LIB_NAME} PROPERTIES LINK_FLAGS "-framework Carbon")
endif ()