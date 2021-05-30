package kr.ac.kumoh.s20160001.shoppingmall
import okhttp3.MultipartBody
import okhttp3.RequestBody
import okhttp3.ResponseBody
import retrofit2.Call
import retrofit2.http.*

interface RetrofitService {
    // Json
    @Multipart
    @POST("/img_upload")
    fun request(
        @Part("clothes") Id:Int?,
        @Part files : MultipartBody.Part):Call<ResponseBody>

    @GET("/image_query")
    fun getimage(
            @Query("id") Id:String?):Call<ResponseBody>

}