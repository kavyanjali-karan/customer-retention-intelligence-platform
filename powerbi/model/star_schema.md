# Star Schema

                dim_date

                    |

dim_customer ---- fact_customer_retention ---- dim_product

                    |

               dim_channel

                    |

               dim_region

Fact

fact_customer_retention

Dimensions

dim_customer

dim_date

dim_product

dim_channel

dim_region