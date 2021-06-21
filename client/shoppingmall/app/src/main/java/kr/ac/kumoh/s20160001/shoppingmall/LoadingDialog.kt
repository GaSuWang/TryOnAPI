package kr.ac.kumoh.s20160001.shoppingmall

import android.app.Dialog
import android.content.Context
import android.graphics.Color
import android.graphics.drawable.ColorDrawable
import android.view.LayoutInflater
import android.view.View
import android.view.animation.AnimationUtils
import android.widget.ImageView

class LoadingDialog
constructor(context: Context):Dialog(context){
    init{
        setCanceledOnTouchOutside(false)
        window!!.setBackgroundDrawable(ColorDrawable(Color.TRANSPARENT))
        setContentView(R.layout.dialog_loading)
    }

    override fun setContentView(view: View) {
        super.setContentView(view)
    }

}
