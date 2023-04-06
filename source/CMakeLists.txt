############################################################
# Create the QPixRTD library
############################################################

# file(GLOB SOURCES "*.cpp")

# # generate ROOT dictionary
# ROOT_GENERATE_DICTIONARY(QPixRTDDict ROOTFileManager.h LINKDEF LinkDef.h)

##Generate the static library from the library sources
add_executable(temp temp.cpp)
target_link_libraries(temp ${ROOT_LIBRARIES})
# enable_language(CUDA)
# include(CheckLanguage)
# check_language(CUDA)

add_executable(filtNeutino neutrinoFilt.cpp)
target_link_libraries(filtNeutino ${ROOT_LIBRARIES})

add_executable(combNeutrinoRam neutrinoCombRam.cpp)
target_link_libraries(combNeutrinoRam ${ROOT_LIBRARIES})

add_executable(anaNeutrino neutAna.cpp)
target_link_libraries(anaNeutrino ${ROOT_LIBRARIES})