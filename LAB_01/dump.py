def move_left(rectangles, rect_count):  # I made a beautiful bug here. I loved it. 
    '''This function isn't doing what it's supposed todo but I like what it's doing currently'''
    if rect_count <= 1:
        return
    
    first_color = rectangles[0].color
    first_h = rectangles[0].rect.height
    first_y = rectangles[0].rect.y
    
    for i in range(1, rect_count-1):
        rectangles[i].color = rectangles[i+1].color
        rectangles[i].height = rectangles[i+1].rect.height
        rectangles[i].y = rectangles[i+1].rect.y
        
    rectangles[-1].color = first_color
    rectangles[-1].rect.height = first_h
    rectangles[-1].rect.y = first_y


# def make_same_height(rectangles, rect_count):
#     if rect_count <= 1:
#         return
    
#     smallest_height = rectangles[0].rect.height
#     print(smallest_height)
#     for i in range(rect_count-1):
#         if rectangles[i].rect.height < smallest_height:
#             smallest_height = rectangles[i].rect.height
            
#     for r in range(rect_count-1):
#         rectangles[r].rect.height = smallest_height
#         print(rectangles[r].rect.y)


# def sort_manually(rectangles, rect_count):
#     pass


# def make_same_color(rectangles, rect_count):
#     # give all displayed rectangles the same color as the right-most rectangle
#     right_color = rectangles[-1].color
#     for i in range(rect_count-1):
#         rectangles[i].color = right_color