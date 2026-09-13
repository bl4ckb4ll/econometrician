# Convention specification

## Vehicle orientation

- **driver**: vehicle left when seated facing forward;
- **passenger**: vehicle right when seated facing forward;
- **front**: toward the front bumper;
- **rear**: toward the cab/rearward along the vehicle.

## Cam rotation

The benchmark's fixed convention is:

> clockwise/counterclockwise is named while looking **from the rear of the truck toward the front**.

This is not retroactively imposed on historical statements. A historical phrase explicitly made from the front looking back is stored with that original viewpoint; its CW/CCW word reverses under the benchmark viewpoint.

Cam rotation and pivot motion are separate fields:

- **outward** = away from engine / vehicle centerline;
- **inward** = toward engine / vehicle centerline.

An outward pivot move does not, by itself, determine CW or CCW without the cam location, clock phase, and viewpoint.

## Alignment signs

The recovered model conventions use:

- positive camber: top of tire outward;
- positive caster: top steering axis/pivot rearward;
- recovered script steering sign: positive steering-wheel/road-wheel yaw to the right.

The last item is a code convention, not authority to relabel an ambiguous handwritten row.

## Sweep coordinates

Recovered script:

- `alpha`: steering-wheel rotation, radians, positive right;
- `theta`: individual road-wheel yaw, radians, positive right;
- `gamma`: measured camber, degrees;
- row vector `[-1.59, -1, -0.5, 0, 0.5, 1, 1.59]` steering-wheel turns.

Because the direct Sep10 passenger sequence conflicts with the script's row labels, both are preserved. The benchmark does not resolve the conflict by changing a sign.

## Jacobian indexing

Candidate 14×26 observation Jacobian:

- rows 0–6: driver camber rows;
- rows 7–13: passenger camber rows;
- columns are named in `data/jacobian_spec.json` and never referenced only by integer in public-facing calculations;
- each row/column has a unit;
- the basis is the coordinate basis of those named variables, not a claimed natural basis of suspension configuration space.
