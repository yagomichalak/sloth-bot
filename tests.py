#z!eval
from mysqldb import the_database

async def convert_everyone() -> None:
    mycursor, db = await the_database()
    await mycursor.excute("""
    SELECT user_id, sloth_class, change_class_ts,
    protected, has_potion, hacked,
    knocked_out, skills_used, knife_sharpness_stack,
    wired, tribe, frogged
    """)

    users = await mycursor.fetchall()

    await mycursor.execute("""
    INSERT INTO SlothProfile (

    )
    """)
""""""

# select * from information_schema.table_constraints where constraint_schema = 'Sloth'

315112274140332032, "autism-spectrum Tribe", "Are you diagnosed with autism or just curious about it? Maybe join the tribe for info and fun!", "🤝😃", NULL, "https://forms.gle/MT1yKH6pL2zN6tb68", "315112274140332032-autism-spectrum-tribe"

 INSERT INTO UserCurrency (
     user_id
     ) VALUES (
         (315112274140332032), (368072947866271755), (401774791322894336), (409466241171062794), (588843441430069260),
        (647452832852869120), (685437115282096132), (687665157429788716), (711922866521767957), (737179660085100586), 
         (754678627265675325), (816585307360985098), (817584081264836668), (818954612068450314), (820290993692737573)
         )
     )


 INSERT INTO UserCurrency (
     user_id
     ) VALUES (
     (293401961045295116,), (315112274140332032,), (368072947866271755,), 
     (401774791322894336,), (409466241171062794,), (588843441430069260,), 
     (647452832852869120,), (685437115282096132,), (687665157429788716,), 
     (711922866521767957,), (737179660085100586,), (754678627265675325,), 
     (816585307360985098,), (817584081264836668,), (818954612068450314,), 
     (820290993692737573,)
);