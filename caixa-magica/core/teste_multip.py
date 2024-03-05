import multiprocessing

NUMBER_OF_PROCESSES = multiprocessing.cpu_count()
MP_FUNCTION = 'imap_unordered'  # 'imap_unordered' or 'starmap' or 'apply_async'

def process_chunk(a_chunk):
    print(f"processig mp chunk {a_chunk}")
    return a_chunk


map_jobs = [1, 2, 3, 4]

result_sum = 0

if MP_FUNCTION == 'imap_unordered':
    pool = multiprocessing.Pool(processes=NUMBER_OF_PROCESSES)
    for i in pool.imap_unordered(process_chunk, map_jobs):
        print(i)
        result_sum += i
elif MP_FUNCTION == 'starmap':
    pool = multiprocessing.Pool(processes=NUMBER_OF_PROCESSES)
    try:
        map_jobs = [(i, ) for i in map_jobs]
        result_sum = pool.starmap(process_chunk, map_jobs)
        result_sum = sum(result_sum)
    finally:
        pool.close()
        pool.join()
elif MP_FUNCTION == 'apply_async':
    with multiprocessing.Pool(processes=NUMBER_OF_PROCESSES) as pool:
        result_sum = [pool.apply_async(process_chunk, [i, ]).get() for i in map_jobs]
    result_sum = sum(result_sum)
print(f"result_sum is {result_sum}")
