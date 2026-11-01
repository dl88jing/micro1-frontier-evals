When two aware datetimes share the identical tzinfo object, Python subtracts them as naive wall times → 26 hours.
`timestamp()` difference is absolute elapsed time → 25 hours across the lost spring-forward hour.
The non-existent 02:30 is still constructible; fold=0 keeps UTC-8.
01:00→04:00 local spans 7200 absolute seconds, not 10800.
