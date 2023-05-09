echo 'ni hao'

## neutrino analysis files to move
cp ./output_images/*pdf ../../research/qp_dissertation/images/

## digital simulation files to move
## note: fast and slow refer to high and low variance on ASIC local oscillator frq
# fast simulation files
cp ./output_images/mp60_16_fast_local_stack.pdf ../../research/qp_dissertation/images/example_16_local_stack.pdf
cp ./output_images/mp60_16_fast_remote_stack.pdf ../../research/qp_dissertation/images/example_16_remote_stack.pdf
cp ./output_images/mp60_16_fast_remote_transactions.pdf ../../research/qp_dissertation/images/example_16_remote_transact.pdf
cp ./output_images/mp60_16_fast_route_fits.pdf ../../research/qp_dissertation/images/example_16_route_fits.pdf

cp ./output_images/mp60_64_fast_local_stack.pdf ../../research/qp_dissertation/images/example_64_local_stack.pdf
cp ./output_images/mp60_64_fast_remote_stack.pdf ../../research/qp_dissertation/images/example_64_remote_stack.pdf
cp ./output_images/mp60_64_fast_remote_transactions.pdf ../../research/qp_dissertation/images/example_64_remote_transact.pdf
cp ./output_images/mp60_64_fast_route_fits.pdf ../../research/qp_dissertation/images/example_64_route_fits.pdf

cp ./output_images/mp60_140_fast_local_stack.pdf ../../research/qp_dissertation/images/example_140_local_stack.pdf
cp ./output_images/mp60_140_fast_remote_stack.pdf ../../research/qp_dissertation/images/example_140_remote_stack.pdf
cp ./output_images/mp60_140_fast_remote_transactions.pdf ../../research/qp_dissertation/images/example_140_remote_transact.pdf
cp ./output_images/mp60_140_fast_route_fits.pdf ../../research/qp_dissertation/images/example_140_route_fits.pdf

cp ./output_images/mp60_256_fast_local_stack.pdf ../../research/qp_dissertation/images/example_256_local_stack.pdf
cp ./output_images/mp60_256_fast_remote_stack.pdf ../../research/qp_dissertation/images/example_256_remote_stack.pdf
cp ./output_images/mp60_256_fast_remote_transactions.pdf ../../research/qp_dissertation/images/example_256_remote_transact.pdf
cp ./output_images/mp60_256_fast_route_fits.pdf ../../research/qp_dissertation/images/example_256_route_fits.pdf

# slow simulation files
cp ./output_images/mp60_16_slow_local_stack.pdf ../../research/qp_dissertation/images/example_16_local_stack_slow.pdf
cp ./output_images/mp60_16_slow_remote_stack.pdf ../../research/qp_dissertation/images/example_16_remote_stack_slow.pdf
cp ./output_images/mp60_16_slow_remote_transactions.pdf ../../research/qp_dissertation/images/example_16_remote_transact_slow.pdf
cp ./output_images/mp60_16_slow_route_fits.pdf ../../research/qp_dissertation/images/example_16_route_fits_slow.pdf

cp ./output_images/mp60_64_slow_local_stack.pdf ../../research/qp_dissertation/images/example_64_local_stack_slow.pdf
cp ./output_images/mp60_64_slow_remote_stack.pdf ../../research/qp_dissertation/images/example_64_remote_stack_slow.pdf
cp ./output_images/mp60_64_slow_remote_transactions.pdf ../../research/qp_dissertation/images/example_64_remote_transact_slow.pdf
cp ./output_images/mp60_64_slow_route_fits.pdf ../../research/qp_dissertation/images/example_64_route_fits_slow.pdf

cp ./output_images/mp60_140_slow_local_stack.pdf ../../research/qp_dissertation/images/example_140_local_stack_slow.pdf
cp ./output_images/mp60_140_slow_remote_stack.pdf ../../research/qp_dissertation/images/example_140_remote_stack_slow.pdf
cp ./output_images/mp60_140_slow_remote_transactions.pdf ../../research/qp_dissertation/images/example_140_remote_transact_slow.pdf
cp ./output_images/mp60_140_slow_route_fits.pdf ../../research/qp_dissertation/images/example_140_route_fits_slow.pdf

cp ./output_images/mp60_256_slow_local_stack.pdf ../../research/qp_dissertation/images/example_256_local_stack_slow.pdf
cp ./output_images/mp60_256_slow_remote_stack.pdf ../../research/qp_dissertation/images/example_256_remote_stack_slow.pdf
cp ./output_images/mp60_256_slow_remote_transactions.pdf ../../research/qp_dissertation/images/example_256_remote_transact_slow.pdf
cp ./output_images/mp60_256_slow_route_fits.pdf ../../research/qp_dissertation/images/example_256_route_fits_slow.pdf

## move all of the tex files we create
cp ./output_images/*tex ../../research/qp_dissertation/chapters/tables/