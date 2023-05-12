############################################################
# Create the neutAna
############################################################

add_executable(combNeutrinoRam neutrinoCombRam.cpp)
target_link_libraries(combNeutrinoRam ${ROOT_LIBRARIES})

add_executable(anaNeutrino neutAna.cpp)
target_link_libraries(anaNeutrino ${ROOT_LIBRARIES})

add_executable(fixHadNeut fixHadNeutrino.cpp)
target_link_libraries(fixHadNeut ${ROOT_LIBRARIES})

add_executable(graphsNeutrino neutGraphs.cpp)
target_link_libraries(graphsNeutrino ${ROOT_LIBRARIES})